/* ------------------------------------------------------------
name: "accordion"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Accordion -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Accordion_H__
#define  __Accordion_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Accordion
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

static float Accordion_faustpower2_f(float value) {
	return value * value;
}

class Accordion : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	float fConst2;
	float fRec3[2];
	FAUSTFLOAT fHslider1;
	float fConst3;
	FAUSTFLOAT fHslider2;
	float fConst4;
	float fRec4[2];
	float fVec2[2];
	float fConst5;
	int IOTA0;
	float fVec3[4096];
	float fConst6;
	float fRec5[2];
	float fVec4[2];
	float fVec5[4096];
	float fRec6[2];
	float fVec6[2];
	float fVec7[4096];
	float fRec7[2];
	float fVec8[2];
	float fVec9[4096];
	FAUSTFLOAT fHslider3;
	float fRec1[3];
	float fVec10[2];
	float fConst7;
	float fConst8;
	float fConst9;
	float fRec0[2];
	
 public:
	Accordion() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Accordion -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "accordion.dsp");
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
		m->declare("name", "accordion");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/sawN:author", "Julius O. Smith III");
		m->declare("oscillators.lib/sawN:license", "STK-4.3");
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
		fConst2 = 1.0f / std::max<float>(1.0f, 0.12f * fConst0);
		fConst3 = 0.15f / std::max<float>(1.0f, 0.1f * fConst0);
		fConst4 = 1.0f / fConst0;
		fConst5 = 0.25f * fConst0;
		fConst6 = 0.45f * fConst0;
		fConst7 = 1.0f / std::tan(345.5752f / fConst0);
		fConst8 = 1.0f - fConst7;
		fConst9 = 1.0f / (fConst7 + 1.0f);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(2.8e+03f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.06f);
		fHslider2 = FAUSTFLOAT(2.2e+02f);
		fHslider3 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec2[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec3[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec4[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fVec2[l5] = 0.0f;
		}
		IOTA0 = 0;
		for (int l6 = 0; l6 < 4096; l6 = l6 + 1) {
			fVec3[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec5[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fVec4[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 4096; l9 = l9 + 1) {
			fVec5[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec6[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fVec6[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 4096; l12 = l12 + 1) {
			fVec7[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec7[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fVec8[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 4096; l15 = l15 + 1) {
			fVec9[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 3; l16 = l16 + 1) {
			fRec1[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 2; l17 = l17 + 1) {
			fVec10[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			fRec0[l18] = 0.0f;
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
	
	virtual Accordion* clone() {
		return new Accordion();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("accordion");
		ui_interface->addHorizontalSlider("bellows", &fHslider1, FAUSTFLOAT(0.06f), FAUSTFLOAT(0.01f), FAUSTFLOAT(0.5f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("tone", &fHslider0, FAUSTFLOAT(2.8e+03f), FAUSTFLOAT(1e+03f), FAUSTFLOAT(6e+03f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = 2.0f * (1.0f - 1.0f / Accordion_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / fSlow0;
		float fSlow3 = (fSlow2 + -1.4142135f) / fSlow0 + 1.0f;
		float fSlow4 = 1.0f / ((fSlow2 + 1.4142135f) / fSlow0 + 1.0f);
		float fSlow5 = float(fButton0);
		int iSlow6 = fSlow5 == 0.0f;
		float fSlow7 = std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow8 = 1.0f / fSlow7;
		float fSlow9 = float(fHslider2);
		float fSlow10 = std::max<float>(1.0035f * fSlow9, 23.44895f);
		float fSlow11 = std::max<float>(2e+01f, std::fabs(fSlow10));
		float fSlow12 = fConst4 * fSlow11;
		float fSlow13 = fConst5 / fSlow11;
		float fSlow14 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst6 / fSlow10));
		int iSlow15 = int(fSlow14);
		float fSlow16 = std::floor(fSlow14);
		float fSlow17 = fSlow16 + (1.0f - fSlow14);
		float fSlow18 = std::max<float>(0.9965f * fSlow9, 23.44895f);
		float fSlow19 = std::max<float>(2e+01f, std::fabs(fSlow18));
		float fSlow20 = fConst4 * fSlow19;
		float fSlow21 = fConst5 / fSlow19;
		float fSlow22 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst6 / fSlow18));
		int iSlow23 = int(fSlow22);
		int iSlow24 = iSlow23 + 1;
		float fSlow25 = std::floor(fSlow22);
		float fSlow26 = fSlow22 - fSlow25;
		float fSlow27 = fSlow25 + (1.0f - fSlow22);
		int iSlow28 = iSlow15 + 1;
		float fSlow29 = fSlow14 - fSlow16;
		float fSlow30 = std::max<float>(0.5f * fSlow9, 23.44895f);
		float fSlow31 = std::max<float>(2e+01f, std::fabs(fSlow30));
		float fSlow32 = fConst4 * fSlow31;
		float fSlow33 = fConst5 / fSlow31;
		float fSlow34 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst6 / fSlow30));
		int iSlow35 = int(fSlow34);
		int iSlow36 = iSlow35 + 1;
		float fSlow37 = std::floor(fSlow34);
		float fSlow38 = fSlow34 - fSlow37;
		float fSlow39 = fSlow37 + (1.0f - fSlow34);
		float fSlow40 = std::max<float>(2.004f * fSlow9, 23.44895f);
		float fSlow41 = std::max<float>(2e+01f, std::fabs(fSlow40));
		float fSlow42 = fConst4 * fSlow41;
		float fSlow43 = fConst5 / fSlow41;
		float fSlow44 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst6 / fSlow40));
		int iSlow45 = int(fSlow44);
		int iSlow46 = iSlow45 + 1;
		float fSlow47 = std::floor(fSlow44);
		float fSlow48 = fSlow44 - fSlow47;
		float fSlow49 = fSlow47 + (1.0f - fSlow44);
		float fSlow50 = 1.0f / fSlow11;
		float fSlow51 = 1.0f / fSlow19;
		float fSlow52 = 0.47619048f * float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow5;
			iRec2[0] = iSlow6 * (iRec2[1] + 1);
			fRec3[0] = fSlow5 + fRec3[1] * float(fVec1[1] >= fSlow5);
			int iTemp0 = 1 - iVec0[1];
			float fTemp1 = ((iTemp0) ? 0.0f : fSlow12 + fRec4[1]);
			fRec4[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = Accordion_faustpower2_f(2.0f * fRec4[0] + -1.0f);
			fVec2[0] = fTemp2;
			float fTemp3 = fTemp2 - fVec2[1];
			float fTemp4 = float(iVec0[1]);
			float fTemp5 = fSlow13 * fTemp4 * fTemp3;
			fVec3[IOTA0 & 4095] = fTemp5;
			float fTemp6 = ((iTemp0) ? 0.0f : fSlow20 + fRec5[1]);
			fRec5[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = Accordion_faustpower2_f(2.0f * fRec5[0] + -1.0f);
			fVec4[0] = fTemp7;
			float fTemp8 = fTemp7 - fVec4[1];
			float fTemp9 = fSlow21 * fTemp4 * fTemp8;
			fVec5[IOTA0 & 4095] = fTemp9;
			float fTemp10 = ((iTemp0) ? 0.0f : fSlow32 + fRec6[1]);
			fRec6[0] = fTemp10 - std::floor(fTemp10);
			float fTemp11 = Accordion_faustpower2_f(2.0f * fRec6[0] + -1.0f);
			fVec6[0] = fTemp11;
			float fTemp12 = fSlow33 * fTemp4 * (fTemp11 - fVec6[1]);
			fVec7[IOTA0 & 4095] = fTemp12;
			float fTemp13 = ((iTemp0) ? 0.0f : fSlow42 + fRec7[1]);
			fRec7[0] = fTemp13 - std::floor(fTemp13);
			float fTemp14 = Accordion_faustpower2_f(2.0f * fRec7[0] + -1.0f);
			fVec8[0] = fTemp14;
			float fTemp15 = fSlow43 * fTemp4 * (fTemp14 - fVec8[1]);
			fVec9[IOTA0 & 4095] = fTemp15;
			fRec1[0] = fSlow52 * (fConst5 * fTemp4 * (fSlow51 * fTemp8 + fSlow50 * fTemp3) + 0.4f * (fTemp15 + (-0.45f - (fSlow49 * fVec9[(IOTA0 - iSlow45) & 4095] + fSlow48 * fVec9[(IOTA0 - iSlow46) & 4095]))) + 0.3f * (fTemp12 + (-0.45f - (fSlow39 * fVec7[(IOTA0 - iSlow35) & 4095] + fSlow38 * fVec7[(IOTA0 - iSlow36) & 4095]))) + (-0.9f - (fSlow29 * fVec3[(IOTA0 - iSlow28) & 4095] + fSlow27 * fVec5[(IOTA0 - iSlow23) & 4095] + fSlow26 * fVec5[(IOTA0 - iSlow24) & 4095] + fSlow17 * fVec3[(IOTA0 - iSlow15) & 4095]))) * std::max<float>(0.0f, std::min<float>(fSlow8 * fRec3[0], std::max<float>(fConst3 * (fSlow7 - fRec3[0]) + 1.0f, 0.85f)) * (1.0f - fConst2 * float(iRec2[0]))) - fSlow4 * (fSlow3 * fRec1[2] + fSlow1 * fRec1[1]);
			float fTemp16 = fSlow4 * (fRec1[2] + fRec1[0] + 2.0f * fRec1[1]);
			fVec10[0] = fTemp16;
			fRec0[0] = -(fConst9 * (fConst8 * fRec0[1] - fConst7 * (fTemp16 - fVec10[1])));
			float fTemp17 = 0.46f * fRec0[0];
			output0[i0] = FAUSTFLOAT(fTemp17);
			output1[i0] = FAUSTFLOAT(fTemp17);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			fRec3[1] = fRec3[0];
			fRec4[1] = fRec4[0];
			fVec2[1] = fVec2[0];
			IOTA0 = IOTA0 + 1;
			fRec5[1] = fRec5[0];
			fVec4[1] = fVec4[0];
			fRec6[1] = fRec6[0];
			fVec6[1] = fVec6[0];
			fRec7[1] = fRec7[0];
			fVec8[1] = fVec8[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fVec10[1] = fVec10[0];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
