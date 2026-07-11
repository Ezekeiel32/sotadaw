/* ------------------------------------------------------------
name: "supersaw"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Supersaw -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Supersaw_H__
#define  __Supersaw_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Supersaw
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float Supersaw_faustpower2_f(float value) {
	return value * value;
}

class Supersaw : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec2[2];
	FAUSTFLOAT fHslider1;
	float fRec3[2];
	FAUSTFLOAT fHslider2;
	float fConst2;
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	float fConst3;
	float fRec4[2];
	float fRec6[2];
	float fRec8[2];
	float fRec10[2];
	float fRec12[2];
	float fRec14[2];
	float fRec16[2];
	FAUSTFLOAT fHslider5;
	float fVec1[2];
	float fRec1[2];
	float fRec0[3];
	
 public:
	Supersaw() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Supersaw -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "supersaw.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "supersaw");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 3.1415927f / fConst0;
		fConst2 = 0.2f / std::max<float>(1.0f, 0.2f * fConst0);
		fConst3 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(7e+03f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.3f);
		fHslider2 = FAUSTFLOAT(0.02f);
		fHslider3 = FAUSTFLOAT(0.02f);
		fHslider4 = FAUSTFLOAT(2.2e+02f);
		fHslider5 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec2[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec3[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec4[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec6[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec8[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec10[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec12[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec14[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec16[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fVec1[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec1[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec0[l12] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual Supersaw* clone() {
		return new Supersaw();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("supersaw");
		ui_interface->addHorizontalSlider("attack", &fHslider2, FAUSTFLOAT(0.02f), FAUSTFLOAT(0.001f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("cutoff", &fHslider0, FAUSTFLOAT(7e+03f), FAUSTFLOAT(5e+02f), FAUSTFLOAT(1.2e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("detune", &fHslider3, FAUSTFLOAT(0.02f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.1f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider4, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("release", &fHslider1, FAUSTFLOAT(0.3f), FAUSTFLOAT(0.02f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = 2.0f * (1.0f - 1.0f / Supersaw_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / fSlow0;
		float fSlow3 = (fSlow2 + -1.0f) / fSlow0 + 1.0f;
		float fSlow4 = (fSlow2 + 1.0f) / fSlow0 + 1.0f;
		float fSlow5 = 1.0f / fSlow4;
		float fSlow6 = float(fButton0);
		int iSlow7 = fSlow6 == 0.0f;
		float fSlow8 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow9 = std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow10 = 1.0f / fSlow9;
		float fSlow11 = float(fHslider3);
		float fSlow12 = 2.0f * fSlow11;
		float fSlow13 = float(fHslider4);
		float fSlow14 = std::max<float>(1.1920929e-07f, std::fabs(fSlow13 * (1.0f - fSlow12)));
		float fSlow15 = fConst3 * fSlow14;
		float fSlow16 = 1.0f - fConst0 / fSlow14;
		float fSlow17 = 3.0f * fSlow11;
		float fSlow18 = std::max<float>(1.1920929e-07f, std::fabs(fSlow13 * (1.0f - fSlow17)));
		float fSlow19 = fConst3 * fSlow18;
		float fSlow20 = 1.0f - fConst0 / fSlow18;
		float fSlow21 = std::max<float>(1.1920929e-07f, std::fabs(fSlow13 * (1.0f - fSlow11)));
		float fSlow22 = fConst3 * fSlow21;
		float fSlow23 = 1.0f - fConst0 / fSlow21;
		float fSlow24 = std::max<float>(1.1920929e-07f, std::fabs(fSlow13));
		float fSlow25 = fConst3 * fSlow24;
		float fSlow26 = 1.0f - fConst0 / fSlow24;
		float fSlow27 = std::max<float>(1.1920929e-07f, std::fabs(fSlow13 * (fSlow11 + 1.0f)));
		float fSlow28 = fConst3 * fSlow27;
		float fSlow29 = 1.0f - fConst0 / fSlow27;
		float fSlow30 = std::max<float>(1.1920929e-07f, std::fabs(fSlow13 * (fSlow12 + 1.0f)));
		float fSlow31 = fConst3 * fSlow30;
		float fSlow32 = 1.0f - fConst0 / fSlow30;
		float fSlow33 = std::max<float>(1.1920929e-07f, std::fabs(fSlow13 * (fSlow17 + 1.0f)));
		float fSlow34 = fConst3 * fSlow33;
		float fSlow35 = 1.0f - fConst0 / fSlow33;
		float fSlow36 = 0.14285715f * float(fHslider5);
		float fSlow37 = 1.0f - fSlow2;
		float fSlow38 = 1.0f / (fSlow2 + 1.0f);
		float fSlow39 = 0.869f / fSlow4;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow6;
			iRec2[0] = iSlow7 * (iRec2[1] + 1);
			fRec3[0] = fSlow6 + fRec3[1] * float(fVec0[1] >= fSlow6);
			float fTemp0 = fSlow15 + fRec4[1] + -1.0f;
			int iTemp1 = fTemp0 < 0.0f;
			float fTemp2 = fSlow15 + fRec4[1];
			fRec4[0] = ((iTemp1) ? fTemp2 : fTemp0);
			float fRec5 = ((iTemp1) ? fTemp2 : fSlow15 + fRec4[1] + fSlow16 * fTemp0);
			float fTemp3 = fSlow19 + fRec6[1] + -1.0f;
			int iTemp4 = fTemp3 < 0.0f;
			float fTemp5 = fSlow19 + fRec6[1];
			fRec6[0] = ((iTemp4) ? fTemp5 : fTemp3);
			float fRec7 = ((iTemp4) ? fTemp5 : fSlow19 + fRec6[1] + fSlow20 * fTemp3);
			float fTemp6 = fSlow22 + fRec8[1] + -1.0f;
			int iTemp7 = fTemp6 < 0.0f;
			float fTemp8 = fSlow22 + fRec8[1];
			fRec8[0] = ((iTemp7) ? fTemp8 : fTemp6);
			float fRec9 = ((iTemp7) ? fTemp8 : fSlow22 + fRec8[1] + fSlow23 * fTemp6);
			float fTemp9 = fSlow25 + fRec10[1] + -1.0f;
			int iTemp10 = fTemp9 < 0.0f;
			float fTemp11 = fSlow25 + fRec10[1];
			fRec10[0] = ((iTemp10) ? fTemp11 : fTemp9);
			float fRec11 = ((iTemp10) ? fTemp11 : fSlow25 + fRec10[1] + fSlow26 * fTemp9);
			float fTemp12 = fSlow28 + fRec12[1] + -1.0f;
			int iTemp13 = fTemp12 < 0.0f;
			float fTemp14 = fSlow28 + fRec12[1];
			fRec12[0] = ((iTemp13) ? fTemp14 : fTemp12);
			float fRec13 = ((iTemp13) ? fTemp14 : fSlow28 + fRec12[1] + fSlow29 * fTemp12);
			float fTemp15 = fSlow31 + fRec14[1] + -1.0f;
			int iTemp16 = fTemp15 < 0.0f;
			float fTemp17 = fSlow31 + fRec14[1];
			fRec14[0] = ((iTemp16) ? fTemp17 : fTemp15);
			float fRec15 = ((iTemp16) ? fTemp17 : fSlow31 + fRec14[1] + fSlow32 * fTemp15);
			float fTemp18 = fSlow34 + fRec16[1] + -1.0f;
			int iTemp19 = fTemp18 < 0.0f;
			float fTemp20 = fSlow34 + fRec16[1];
			fRec16[0] = ((iTemp19) ? fTemp20 : fTemp18);
			float fRec17 = ((iTemp19) ? fTemp20 : fSlow34 + fRec16[1] + fSlow35 * fTemp18);
			float fTemp21 = fSlow36 * (2.0f * (fRec17 - (1.0f - (fRec15 + (fRec13 - (1.0f - (fRec11 + (fRec9 - (1.0f - (fRec7 + fRec5))))))))) + -1.0f) * std::max<float>(0.0f, std::min<float>(fSlow10 * fRec3[0], std::max<float>(fConst2 * (fSlow9 - fRec3[0]) + 1.0f, 0.8f)) * (1.0f - fSlow8 * float(iRec2[0])));
			fVec1[0] = fTemp21;
			fRec1[0] = -(fSlow38 * (fSlow37 * fRec1[1] - (fTemp21 + fVec1[1])));
			fRec0[0] = fRec1[0] - fSlow5 * (fSlow3 * fRec0[2] + fSlow1 * fRec0[1]);
			float fTemp22 = fSlow39 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp22);
			output1[i0] = FAUSTFLOAT(fTemp22);
			fVec0[1] = fVec0[0];
			iRec2[1] = iRec2[0];
			fRec3[1] = fRec3[0];
			fRec4[1] = fRec4[0];
			fRec6[1] = fRec6[0];
			fRec8[1] = fRec8[0];
			fRec10[1] = fRec10[0];
			fRec12[1] = fRec12[0];
			fRec14[1] = fRec14[0];
			fRec16[1] = fRec16[0];
			fVec1[1] = fVec1[0];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
