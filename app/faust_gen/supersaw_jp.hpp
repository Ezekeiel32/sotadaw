/* ------------------------------------------------------------
name: "supersaw_jp"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn SupersawJp -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __SupersawJp_H__
#define  __SupersawJp_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS SupersawJp
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

static float SupersawJp_faustpower2_f(float value) {
	return value * value;
}

class SupersawJp : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	FAUSTFLOAT fHslider1;
	float fConst2;
	float fRec1[2];
	float fRec3[2];
	float fRec5[2];
	float fRec7[2];
	float fRec9[2];
	float fRec11[2];
	FAUSTFLOAT fHslider2;
	float fRec13[2];
	float fRec0[3];
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec15[2];
	FAUSTFLOAT fHslider3;
	float fRec16[2];
	FAUSTFLOAT fHslider4;
	float fConst3;
	FAUSTFLOAT fHslider5;
	
 public:
	SupersawJp() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn SupersawJp -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "supersaw_jp.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/name", "Faust Filters Library");
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
		m->declare("name", "supersaw_jp");
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
		fConst2 = 1.0f / fConst0;
		fConst3 = 0.15f / std::max<float>(1.0f, 0.12f * fConst0);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(2.2e+02f);
		fHslider1 = FAUSTFLOAT(0.4f);
		fHslider2 = FAUSTFLOAT(0.8f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider3 = FAUSTFLOAT(0.15f);
		fHslider4 = FAUSTFLOAT(0.004f);
		fHslider5 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fRec1[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fRec3[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec5[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec7[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec9[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec11[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec13[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec0[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fVec0[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			iRec15[l9] = 0;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec16[l10] = 0.0f;
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
	
	virtual SupersawJp* clone() {
		return new SupersawJp();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("supersaw_jp");
		ui_interface->addHorizontalSlider("attack", &fHslider4, FAUSTFLOAT(0.004f), FAUSTFLOAT(0.001f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("detune", &fHslider1, FAUSTFLOAT(0.4f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider0, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("mix", &fHslider2, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("release", &fHslider3, FAUSTFLOAT(0.15f), FAUSTFLOAT(0.02f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = std::tan(fConst1 * fSlow0);
		float fSlow2 = SupersawJp_faustpower2_f(fSlow1);
		float fSlow3 = 2.0f * (1.0f - 1.0f / fSlow2);
		float fSlow4 = 1.0f / fSlow1;
		float fSlow5 = (fSlow4 + -1.4142135f) / fSlow1 + 1.0f;
		float fSlow6 = (fSlow4 + 1.4142135f) / fSlow1 + 1.0f;
		float fSlow7 = 1.0f / fSlow6;
		float fSlow8 = float(fHslider1);
		float fSlow9 = fSlow8 * (fSlow8 * (fSlow8 * (fSlow8 * (fSlow8 * (fSlow8 * (fSlow8 * (fSlow8 * (fSlow8 * (fSlow8 * (10028.731f * fSlow8 + -50818.863f) + 111363.484f) + -138150.67f) + 106649.664f) + -53046.965f) + 17019.951f) + -3425.0837f) + 404.2704f) + -24.187883f) + 0.6717418f) + 0.0030115596f;
		float fSlow10 = std::max<float>(1.1920929e-07f, std::fabs(fSlow0 * (1.0f - 0.06288439f * fSlow9)));
		float fSlow11 = fConst2 * fSlow10;
		float fSlow12 = 1.0f - fConst0 / fSlow10;
		float fSlow13 = std::max<float>(1.1920929e-07f, std::fabs(fSlow0 * (1.0f - 0.11002313f * fSlow9)));
		float fSlow14 = fConst2 * fSlow13;
		float fSlow15 = 1.0f - fConst0 / fSlow13;
		float fSlow16 = std::max<float>(1.1920929e-07f, std::fabs(fSlow0 * (1.0f - 0.01952356f * fSlow9)));
		float fSlow17 = fConst2 * fSlow16;
		float fSlow18 = 1.0f - fConst0 / fSlow16;
		float fSlow19 = std::max<float>(1.1920929e-07f, std::fabs(fSlow0 * (0.01991221f * fSlow9 + 1.0f)));
		float fSlow20 = fConst2 * fSlow19;
		float fSlow21 = 1.0f - fConst0 / fSlow19;
		float fSlow22 = std::max<float>(1.1920929e-07f, std::fabs(fSlow0 * (0.06216538f * fSlow9 + 1.0f)));
		float fSlow23 = fConst2 * fSlow22;
		float fSlow24 = 1.0f - fConst0 / fSlow22;
		float fSlow25 = std::max<float>(1.1920929e-07f, std::fabs(fSlow0 * (0.10745242f * fSlow9 + 1.0f)));
		float fSlow26 = fConst2 * fSlow25;
		float fSlow27 = 1.0f - fConst0 / fSlow25;
		float fSlow28 = float(fHslider2);
		float fSlow29 = 2.0f * (fSlow28 * (1.2841f - 0.73764f * fSlow28) + 0.044372f);
		float fSlow30 = std::max<float>(1.1920929e-07f, std::fabs(fSlow0));
		float fSlow31 = fConst2 * fSlow30;
		float fSlow32 = 1.0f - fConst0 / fSlow30;
		float fSlow33 = 0.99785f - 0.55366f * fSlow28;
		float fSlow34 = float(fButton0);
		int iSlow35 = fSlow34 == 0.0f;
		float fSlow36 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider3));
		float fSlow37 = std::max<float>(1.0f, fConst0 * float(fHslider4));
		float fSlow38 = 1.0f / fSlow37;
		float fSlow39 = 0.1f * (float(fHslider5) / (fSlow2 * fSlow6));
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = fSlow11 + fRec1[1] + -1.0f;
			int iTemp1 = fTemp0 < 0.0f;
			float fTemp2 = fSlow11 + fRec1[1];
			fRec1[0] = ((iTemp1) ? fTemp2 : fTemp0);
			float fRec2 = ((iTemp1) ? fTemp2 : fSlow11 + fRec1[1] + fSlow12 * fTemp0);
			float fTemp3 = fSlow14 + fRec3[1] + -1.0f;
			int iTemp4 = fTemp3 < 0.0f;
			float fTemp5 = fSlow14 + fRec3[1];
			fRec3[0] = ((iTemp4) ? fTemp5 : fTemp3);
			float fRec4 = ((iTemp4) ? fTemp5 : fSlow14 + fRec3[1] + fSlow15 * fTemp3);
			float fTemp6 = fSlow17 + fRec5[1] + -1.0f;
			int iTemp7 = fTemp6 < 0.0f;
			float fTemp8 = fSlow17 + fRec5[1];
			fRec5[0] = ((iTemp7) ? fTemp8 : fTemp6);
			float fRec6 = ((iTemp7) ? fTemp8 : fSlow17 + fRec5[1] + fSlow18 * fTemp6);
			float fTemp9 = fSlow20 + fRec7[1] + -1.0f;
			int iTemp10 = fTemp9 < 0.0f;
			float fTemp11 = fSlow20 + fRec7[1];
			fRec7[0] = ((iTemp10) ? fTemp11 : fTemp9);
			float fRec8 = ((iTemp10) ? fTemp11 : fSlow20 + fRec7[1] + fSlow21 * fTemp9);
			float fTemp12 = fSlow23 + fRec9[1] + -1.0f;
			int iTemp13 = fTemp12 < 0.0f;
			float fTemp14 = fSlow23 + fRec9[1];
			fRec9[0] = ((iTemp13) ? fTemp14 : fTemp12);
			float fRec10 = ((iTemp13) ? fTemp14 : fSlow23 + fRec9[1] + fSlow24 * fTemp12);
			float fTemp15 = fSlow26 + fRec11[1] + -1.0f;
			int iTemp16 = fTemp15 < 0.0f;
			float fTemp17 = fSlow26 + fRec11[1];
			fRec11[0] = ((iTemp16) ? fTemp17 : fTemp15);
			float fRec12 = ((iTemp16) ? fTemp17 : fSlow26 + fRec11[1] + fSlow27 * fTemp15);
			float fTemp18 = fSlow31 + fRec13[1] + -1.0f;
			int iTemp19 = fTemp18 < 0.0f;
			float fTemp20 = fSlow31 + fRec13[1];
			fRec13[0] = ((iTemp19) ? fTemp20 : fTemp18);
			float fRec14 = ((iTemp19) ? fTemp20 : fSlow31 + fRec13[1] + fSlow32 * fTemp18);
			fRec0[0] = fSlow33 * (2.0f * fRec14 + -1.0f) - (fSlow29 * (1.0f - (fRec12 + (fRec10 - (1.0f - (fRec8 + (fRec6 - (1.0f - (fRec4 + fRec2)))))))) + fSlow7 * (fSlow5 * fRec0[2] + fSlow3 * fRec0[1]));
			fVec0[0] = fSlow34;
			iRec15[0] = iSlow35 * (iRec15[1] + 1);
			fRec16[0] = fSlow34 + fRec16[1] * float(fVec0[1] >= fSlow34);
			float fTemp21 = fSlow39 * std::max<float>(0.0f, std::min<float>(fSlow38 * fRec16[0], std::max<float>(fConst3 * (fSlow37 - fRec16[0]) + 1.0f, 0.85f)) * (1.0f - fSlow36 * float(iRec15[0]))) * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp21);
			output1[i0] = FAUSTFLOAT(fTemp21);
			fRec1[1] = fRec1[0];
			fRec3[1] = fRec3[0];
			fRec5[1] = fRec5[0];
			fRec7[1] = fRec7[0];
			fRec9[1] = fRec9[0];
			fRec11[1] = fRec11[0];
			fRec13[1] = fRec13[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fVec0[1] = fVec0[0];
			iRec15[1] = iRec15[0];
			fRec16[1] = fRec16[0];
		}
	}

};

#endif
