/* ------------------------------------------------------------
name: "lead_legato"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn LeadLegato -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __LeadLegato_H__
#define  __LeadLegato_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS LeadLegato
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

class LeadLegatoSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec4[2];
	
  public:
	
	int getNumInputsLeadLegatoSIG0() {
		return 0;
	}
	int getNumOutputsLeadLegatoSIG0() {
		return 1;
	}
	
	void instanceInitLeadLegatoSIG0(int sample_rate) {
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iVec2[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec4[l6] = 0;
		}
	}
	
	void fillLeadLegatoSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec4[0] = (iVec2[1] + iRec4[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec4[0]));
			iVec2[1] = iVec2[0];
			iRec4[1] = iRec4[0];
		}
	}

};

static LeadLegatoSIG0* newLeadLegatoSIG0() { return (LeadLegatoSIG0*)new LeadLegatoSIG0(); }
static void deleteLeadLegatoSIG0(LeadLegatoSIG0* dsp) { delete dsp; }

static float LeadLegato_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0LeadLegatoSIG0[65536];

class LeadLegato : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	float fRec0[2];
	float fConst3;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec1[2];
	FAUSTFLOAT fHslider1;
	float fRec2[2];
	FAUSTFLOAT fHslider2;
	float fConst4;
	float fConst5;
	float fRec6[2];
	float fConst6;
	float fConst7;
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	float fConst8;
	FAUSTFLOAT fHslider5;
	float fRec7[2];
	float fRec5[2];
	float fRec8[2];
	float fRec3[3];
	FAUSTFLOAT fHslider6;
	
 public:
	LeadLegato() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn LeadLegato -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/asr:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "lead_legato.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "lead_legato");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
		m->declare("signals.lib/name", "Faust Signal Routing Library");
		m->declare("signals.lib/version", "1.5.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		LeadLegatoSIG0* sig0 = newLeadLegatoSIG0();
		sig0->instanceInitLeadLegatoSIG0(sample_rate);
		sig0->fillLeadLegatoSIG0(65536, ftbl0LeadLegatoSIG0);
		deleteLeadLegatoSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 44.1f / fConst0;
		fConst2 = 1.0f - fConst1;
		fConst3 = 3.1415927f / fConst0;
		fConst4 = 0.15f / std::max<float>(1.0f, 0.15f * fConst0);
		fConst5 = 5.3f / fConst0;
		fConst6 = 1.0f / std::max<float>(1.0f, 0.2f * fConst0);
		fConst7 = 1.0f / std::max<float>(1.0f, 0.3f * fConst0);
		fConst8 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(3.8e+03f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.22f);
		fHslider2 = FAUSTFLOAT(0.012f);
		fHslider3 = FAUSTFLOAT(0.2f);
		fHslider4 = FAUSTFLOAT(6e+01f);
		fHslider5 = FAUSTFLOAT(2.2e+02f);
		fHslider6 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fRec0[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fVec1[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec1[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec6[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec7[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec5[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec8[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec3[l11] = 0.0f;
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
	
	virtual LeadLegato* clone() {
		return new LeadLegato();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("lead_legato");
		ui_interface->addHorizontalSlider("attack", &fHslider2, FAUSTFLOAT(0.012f), FAUSTFLOAT(0.001f), FAUSTFLOAT(0.5f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("cutoff", &fHslider0, FAUSTFLOAT(3.8e+03f), FAUSTFLOAT(3e+02f), FAUSTFLOAT(1.2e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("freq", &fHslider5, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(3e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider6, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("glide", &fHslider4, FAUSTFLOAT(6e+01f), FAUSTFLOAT(5.0f), FAUSTFLOAT(4e+02f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("release", &fHslider1, FAUSTFLOAT(0.22f), FAUSTFLOAT(0.02f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("vibrato", &fHslider3, FAUSTFLOAT(0.2f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = fConst1 * float(fHslider0);
		float fSlow1 = float(fButton0);
		int iSlow2 = fSlow1 == 0.0f;
		float fSlow3 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow4 = std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow5 = 1.0f / fSlow4;
		float fSlow6 = 0.006f * float(fHslider3);
		float fSlow7 = 0.001f * float(fHslider4);
		int iSlow8 = std::fabs(fSlow7) < 1.1920929e-07f;
		float fSlow9 = ((iSlow8) ? 0.0f : std::exp(-(fConst8 / ((iSlow8) ? 1.0f : fSlow7))));
		float fSlow10 = float(fHslider5) * (1.0f - fSlow9);
		float fSlow11 = 0.5f * float(fHslider6);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fRec0[0] = fSlow0 + fConst2 * fRec0[1];
			float fTemp0 = std::tan(fConst3 * fRec0[0]);
			float fTemp1 = 1.0f / fTemp0;
			float fTemp2 = (fTemp1 + 1.4142135f) / fTemp0 + 1.0f;
			fVec1[0] = fSlow1;
			iRec1[0] = iSlow2 * (iRec1[1] + 1);
			float fTemp3 = float(iRec1[0]);
			fRec2[0] = fSlow1 + fRec2[1] * float(fVec1[1] >= fSlow1);
			int iTemp4 = 1 - iVec0[1];
			float fTemp5 = ((iTemp4) ? 0.0f : fConst5 + fRec6[1]);
			fRec6[0] = fTemp5 - std::floor(fTemp5);
			fRec7[0] = fSlow10 + fSlow9 * fRec7[1];
			float fTemp6 = fRec7[0] * (fSlow6 * std::max<float>(0.0f, std::min<float>(fConst7 * fRec2[0], 1.0f) - fConst6 * fTemp3) * ftbl0LeadLegatoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec6[0]), 65535))] + 1.0f);
			float fTemp7 = ((iTemp4) ? 0.0f : fRec5[1] + fConst8 * fTemp6);
			fRec5[0] = fTemp7 - std::floor(fTemp7);
			float fTemp8 = std::max<float>(1.1920929e-07f, std::fabs(fTemp6));
			float fTemp9 = fRec8[1] + fConst8 * fTemp8;
			float fTemp10 = fTemp9 + -1.0f;
			int iTemp11 = fTemp10 < 0.0f;
			fRec8[0] = ((iTemp11) ? fTemp9 : fTemp10);
			float fRec9 = ((iTemp11) ? fTemp9 : fTemp9 + fTemp10 * (1.0f - fConst0 / fTemp8));
			fRec3[0] = 0.62f * (2.0f * fRec9 + -1.0f) + 0.38f * ftbl0LeadLegatoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec5[0]), 65535))] - (fRec3[2] * ((fTemp1 + -1.4142135f) / fTemp0 + 1.0f) + 2.0f * fRec3[1] * (1.0f - 1.0f / LeadLegato_faustpower2_f(fTemp0))) / fTemp2;
			float fTemp12 = fSlow11 * ((fRec3[2] + fRec3[0] + 2.0f * fRec3[1]) * std::max<float>(0.0f, std::min<float>(fSlow5 * fRec2[0], std::max<float>(fConst4 * (fSlow4 - fRec2[0]) + 1.0f, 0.85f)) * (1.0f - fSlow3 * fTemp3)) / fTemp2);
			output0[i0] = FAUSTFLOAT(fTemp12);
			output1[i0] = FAUSTFLOAT(fTemp12);
			iVec0[1] = iVec0[0];
			fRec0[1] = fRec0[0];
			fVec1[1] = fVec1[0];
			iRec1[1] = iRec1[0];
			fRec2[1] = fRec2[0];
			fRec6[1] = fRec6[0];
			fRec7[1] = fRec7[0];
			fRec5[1] = fRec5[0];
			fRec8[1] = fRec8[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
		}
	}

};

#endif
